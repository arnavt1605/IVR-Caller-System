/**
 * Finalizes a blood request and stores aggregated history
 */

import CallLog from "../models/calllog.js";
import RequestHistory from "../models/requesthistory.js";
import { logAppEvent, logSecurityEvent } from "../utils/logger.js";

export const finalizeRequest = async (req, res) => {
    try {
        const { bloodGroup } = req.body;
        const { organizationId, userId } = req.user;

        if (!bloodGroup) {
            return res.status(400).json({ message: "Blood group is required" });
        }

        // Fetch recent call logs for this org & blood group
        const logs = await CallLog.find({
            organizationId,
            requestId
        });

        const totalCalls = logs.length;
        const answeredCalls = logs.filter(l => l.status === "answered").length;
        const confirmedLogs = logs.filter(l => l.status === "confirmed");

        const confirmedCount = confirmedLogs.length;

        const confirmedDonors = confirmedLogs.map(l => ({
            donorId: l.donorId,
            phone: l.phone
        }));

        await RequestHistory.findByIdAndUpdate(requestId, {
            totalCalls,
            answeredCalls,
            confirmedCount: confirmedDonors.length,
            confirmedDonors,
            status: "COMPLETED"
        });

        const history = await RequestHistory.create({
            organizationId,
            bloodGroup,
            totalCalls,
            answeredCalls,
            confirmedCount,
            confirmedDonors
        });

        await logAppEvent({
            organizationId,
            level: "info",
            message: `Request finalized for blood group ${bloodGroup}`,
            route: req.originalUrl
        });

        await logSecurityEvent({
            organizationId,
            userId,
            action: "FINALIZE_REQUEST",
            ip: req.ip,
            userAgent: req.headers["user-agent"]
        });

        res.status(201).json({
            message: "Request finalized",
            historyId: history._id
        });
    } catch (err) {
        await logAppEvent({
            organizationId: req.user?.organizationId,
            level: "error",
            message: err.message,
            route: req.originalUrl
        });

        res.status(500).json({ message: "Failed to finalize request" });
    }
};
