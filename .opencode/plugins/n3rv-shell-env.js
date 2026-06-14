/**
 * n3rv-shell-env plugin for OpenCode.
 *
 * shell.env hook: injects N3RV_AGENT_SOURCE based on the active OpenCode
 * agent name. Preserves existing value if already set.
 *
 * Agent name → source mapping:
 *   "n3rv"          → "opencode:n3rv"
 *   "sdd-*"         → "opencode:sdd-<phase>"
 *   "git-ops"       → "opencode:git-ops"
 *   "github-ops"    → "opencode:github-ops"
 *   everything else → "opencode:unknown"
 *
 * Uses the OpenCode 1.14.x plugin API: a factory function returning hooks.
 */

const AGENT_SOURCE_MAP = {
  n3rv: "opencode:n3rv",
  "git-ops": "opencode:git-ops",
  "github-ops": "opencode:github-ops",
};

function deriveSource(agentName) {
  if (!agentName || typeof agentName !== "string") return "opencode:unknown";
  if (AGENT_SOURCE_MAP[agentName]) return AGENT_SOURCE_MAP[agentName];
  if (agentName.startsWith("sdd-"))
    return `opencode:sdd-${agentName.replace("sdd-", "")}`;
  return "opencode:unknown";
}

/**
 * Plugin factory (OpenCode 1.14.x API)
 */
export const N3rvShellEnv = async (_ctx) => {
  return {
    /** shell.env hook — runs before each shell subprocess. */
    "shell.env": async (input, output) => {
      try {
        // Never overwrite an already-set value
        if (output.env.N3RV_AGENT_SOURCE) return;

        const agentName = input.agentName ?? input.agent ?? "";
        const source = deriveSource(agentName);
        output.env.N3RV_AGENT_SOURCE = source;
      } catch {
        // Degrade silently — never block OpenCode
      }
    },
  };
};

export default N3rvShellEnv;