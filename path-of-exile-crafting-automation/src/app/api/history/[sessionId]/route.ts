import { NextRequest, NextResponse } from "next/server";
import { db } from "@/db";
import { craftingHistory } from "@/db/schema";
import { eq, desc } from "drizzle-orm";

export const dynamic = "force-dynamic";

export async function GET(_req: NextRequest, { params }: { params: Promise<{ sessionId: string }> }) {
  try {
    const { sessionId } = await params;
    const history = await db
      .select()
      .from(craftingHistory)
      .where(eq(craftingHistory.sessionId, parseInt(sessionId)))
      .orderBy(desc(craftingHistory.createdAt))
      .limit(100);

    return NextResponse.json(history);
  } catch (error) {
    console.error(error);
    return NextResponse.json({ error: "Failed to fetch history" }, { status: 500 });
  }
}
