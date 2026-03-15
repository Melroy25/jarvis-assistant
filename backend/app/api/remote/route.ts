import { NextRequest, NextResponse } from 'next/server';
import { addActions, popActions } from '@/lib/remoteQueue';

export async function POST(request: NextRequest) {
  try {
    const authHeader = request.headers.get('Authorization');
    if (authHeader !== `Bearer ${process.env.JARVIS_API_TOKEN}`) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    const body = await request.json();
    const { actions } = body;
    if (actions && Array.isArray(actions)) {
      addActions(actions);
    }

    return NextResponse.json({ success: true });
  } catch (error) {
    return NextResponse.json({ error: 'Internal Server Error' }, { status: 500 });
  }
}

export async function GET(request: NextRequest) {
  const authHeader = request.headers.get('Authorization');
  if (authHeader !== `Bearer ${process.env.JARVIS_API_TOKEN}`) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }

  const actions = popActions();
  return NextResponse.json({ actions });
}
