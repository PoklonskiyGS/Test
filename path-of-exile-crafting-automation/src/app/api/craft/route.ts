import { NextRequest, NextResponse } from "next/server";
import { db } from "@/db";
import { craftingSessions, craftingHistory } from "@/db/schema";
import { eq } from "drizzle-orm";
import { applyCurrency, checkTargetMet } from "@/lib/crafting-engine";
import type { ItemState } from "@/lib/crafting-engine";
import type { RolledMod } from "@/lib/poe-data";

export const dynamic = "force-dynamic";

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    const { sessionId, currencyId, autoCraft } = body;

    const [session] = await db
      .select()
      .from(craftingSessions)
      .where(eq(craftingSessions.id, sessionId));

    if (!session) {
      return NextResponse.json({ error: "Session not found" }, { status: 404 });
    }

    const currentState: ItemState = {
      base: session.itemBase,
      itemLevel: session.itemLevel,
      rarity: session.rarity as "normal" | "magic" | "rare",
      mods: (session.currentMods as RolledMod[]) || [],
    };

    const targetPrefixes = (session.targetPrefixes as string[]) || [];
    const targetSuffixes = (session.targetSuffixes as string[]) || [];

    if (autoCraft) {
      // Auto-craft: apply currency repeatedly until target is met or max attempts
      const MAX_AUTO_ATTEMPTS = 1000;
      let state = { ...currentState };
      let totalAttempts = 0;
      const currencyUsed: Record<string, number> = (session.currencyUsed as Record<string, number>) || {};
      const historyEntries: Array<{
        sessionId: number;
        currency: string;
        modsBefore: RolledMod[];
        modsAfter: RolledMod[];
        rarityBefore: string;
        rarityAfter: string;
      }> = [];

      while (totalAttempts < MAX_AUTO_ATTEMPTS) {
        const result = applyCurrency(state, currencyId);
        if (!result.success) break;

        historyEntries.push({
          sessionId,
          currency: currencyId,
          modsBefore: result.before.mods,
          modsAfter: result.after.mods,
          rarityBefore: result.before.rarity,
          rarityAfter: result.after.rarity,
        });

        currencyUsed[currencyId] = (currencyUsed[currencyId] || 0) + 1;
        state = result.after;
        totalAttempts++;

        if (checkTargetMet(state.mods, targetPrefixes, targetSuffixes)) {
          break;
        }
      }

      const isComplete = checkTargetMet(state.mods, targetPrefixes, targetSuffixes);

      // Save last 50 history entries to avoid bloat
      const recentHistory = historyEntries.slice(-50);
      if (recentHistory.length > 0) {
        await db.insert(craftingHistory).values(recentHistory);
      }

      const [updated] = await db
        .update(craftingSessions)
        .set({
          rarity: state.rarity,
          currentMods: state.mods,
          currencyUsed,
          attempts: session.attempts + totalAttempts,
          isComplete,
          updatedAt: new Date(),
        })
        .where(eq(craftingSessions.id, sessionId))
        .returning();

      return NextResponse.json({
        session: updated,
        attemptsThisRun: totalAttempts,
        isComplete,
        message: isComplete
          ? `✅ Target achieved in ${totalAttempts} attempt(s)!`
          : `Ran ${totalAttempts} attempt(s) — target not yet met`,
      });
    } else {
      // Single craft
      const result = applyCurrency(currentState, currencyId);

      if (!result.success) {
        return NextResponse.json({ error: result.message }, { status: 400 });
      }

      const currencyUsed: Record<string, number> = (session.currencyUsed as Record<string, number>) || {};
      currencyUsed[currencyId] = (currencyUsed[currencyId] || 0) + 1;

      const isComplete = checkTargetMet(result.after.mods, targetPrefixes, targetSuffixes);

      await db.insert(craftingHistory).values({
        sessionId,
        currency: currencyId,
        modsBefore: result.before.mods,
        modsAfter: result.after.mods,
        rarityBefore: result.before.rarity,
        rarityAfter: result.after.rarity,
      });

      const [updated] = await db
        .update(craftingSessions)
        .set({
          rarity: result.after.rarity,
          currentMods: result.after.mods,
          currencyUsed,
          attempts: session.attempts + 1,
          isComplete,
          updatedAt: new Date(),
        })
        .where(eq(craftingSessions.id, sessionId))
        .returning();

      return NextResponse.json({
        session: updated,
        attemptsThisRun: 1,
        isComplete,
        message: result.message,
      });
    }
  } catch (error) {
    console.error(error);
    return NextResponse.json({ error: "Crafting failed" }, { status: 500 });
  }
}
