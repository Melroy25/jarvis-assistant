// Simple in-memory queue for remote actions
// In a production environment, this should be replaced with Redis or a database
// for persistence across Vercel serverless function invocations.

interface RemoteAction {
  intent: string;
  parameters: any;
}

let pendingActions: RemoteAction[] = [];

export function addActions(actions: RemoteAction[]) {
  pendingActions.push(...actions);
  console.log(`[QUEUE] Added ${actions.length} actions. Current size: ${pendingActions.length}`);
}

export function popActions(): RemoteAction[] {
  const actions = [...pendingActions];
  pendingActions = [];
  return actions;
}
