
// Defines routes related to IVR call operations


import express from "express";
import { triggerCalls } from "../controllers/call.controller.js";
import { authMiddleware } from "../middleware/auth.middleware.js";

const router = express.Router();

// Only authenticated users can trigger calls
router.post("/trigger", authMiddleware, triggerCalls);

export default router;
