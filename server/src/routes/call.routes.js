
// Defines routes related to IVR call operations


import express from "express";
import { triggerCalls } from "../controllers/call.controller.js";
import { authMiddleware } from "../middleware/auth.middleware.js";
import { requireRole } from "../middleware/role.middlerware.js";

const router = express.Router();

// Only authenticated users can trigger calls
router.post("/trigger", authMiddleware, requireRole(["admin"]), triggerCalls); // Only admins can trigger calls

export default router;
