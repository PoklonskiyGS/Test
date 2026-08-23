import { NextRequest, NextResponse } from "next/server";
import { db } from "@/db";
import { craftingSessions } from "@/db/schema";
import { desc } from "drizzle-orm";

export const dynamic = "force-dynamic";

export async function GET() {
  try {
    const sessions = await db
      .select()
      .from(craftingSessions)
      .orderBy(desc(craftingSessions.createdAt))
      .limit(50);
    return NextResponse.json(sessions);
  } catch (error) {
    console.error(error);
    return NextResponse.json({ error: "Failed to fetch sessions" }, { status: 500 });
  }
}

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    const { name, itemBase, itemType, itemLevel, targetPrefixes, targetSuffixes } = body;

    const [session] = await db
      .insert(craftingSessions)
      .values({
        name: name || "New Crafting Session",
        itemBase,
        itemType,
        itemLevel: itemLevel || 80,
        rarity: "normal",
        currentMods: [],
        targetPrefixes: targetPrefixes || [],
        targetSuffixes: targetSuffixes || [],
        currencyUsed: {},
        attempts: 0,
        isComplete: false,
      })
      .returning();

    return NextResponse.json(session);
  } catch (error) {
    console.error(error);
    return NextResponse.json({ error: "Failed to create session" }, { status: 500 });
  }
}
