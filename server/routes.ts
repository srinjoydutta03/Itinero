import type { Express } from "express";
import { createServer, type Server } from "http";
import { createProxyMiddleware } from "http-proxy-middleware";
import { storage } from "./storage";

// The FastAPI backend port — must match the uvicorn port
const BACKEND_URL = process.env.BACKEND_URL || "http://127.0.0.1:8000";

export async function registerRoutes(
  httpServer: Server,
  app: Express
): Promise<Server> {
  // ── Proxy all /api/* requests to the FastAPI backend ────────────────────
  app.use(
    createProxyMiddleware({
      target: BACKEND_URL,
      changeOrigin: true,
      pathFilter: "/api",
      // timeout for long-running agent calls (2 minutes)
      proxyTimeout: 120_000,
      on: {
        error: (err, _req, res) => {
          console.error("[proxy] Error proxying to backend:", err.message);
          if ("writeHead" in res && typeof res.writeHead === "function") {
            (res as any).writeHead(502, { "Content-Type": "application/json" });
            (res as any).end(
              JSON.stringify({
                message: `Backend unavailable: ${err.message}. Is the FastAPI server running on ${BACKEND_URL}?`,
              }),
            );
          }
        },
      },
    }),
  );

  return httpServer;
}
