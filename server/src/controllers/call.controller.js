// Handles IVR call triggering logic for for blood request

import { selectDonorForCall } from "../services/donor.service";
import CallLog from "../models/calllog";
import Donor from "../models/donor";
import { logAppEvent, logSecurityEvent } from "../utils/logger";
import { makeIVRCall } from "../services/twilio.service.js";
import { RequestHistory } from "../models/requesthistory";

export const triggerCalls = async (req, res) => {
    try {
        const { bloodGroup, limit } = req.body;
        const organizationId = req.user.organizationId;

        if (!bloodGroup) {
            return res.status(400).json({ message: "Blood group is required" })
        }

        const donors = await selectDonorForCall({ organizationId, bloodGroup, limit });

        const request = await RequestHistory.create({
            organizationId,
            bloodGroup,
            status: "in_progress",
        });

        const requestId = request._id;


        //App log
        await logAppEvent({
            organizationId,
            level: "info",
            message: `Triggered calls for blood group ${bloodGroup}`,
            route: req.originalUrl
        });

        //Security log
        await logSecurityEvent({
            organizationId,
            userId: req.user.id,
            action: "trigger_calls",
            ip: req.ip,
            userAgent: req.headers["user-agent"]
        });


        if (donors.length === 0) {
            return res.status(404).json({ message: "No donors found", donorsCalled: 0 })
        }

        for (const donor of donors) {
            await CallLog.create({
                organizationId,
                requestId,
                donorId: donor._id,
                phone: donor.phone,
                status: "initiated",
            });

            // Make call using twilio
            await makeIVRCall({
                to: donor.phone,
                callbackURL: `${process.env.BASE_URL}/api/twilio/voice?logId=${log._id}`
            });

            await Donor.updateOne(
                { _id: donor._id },
                {
                    $set: { lastCalledAt: new Date() },
                    $inc: { totalCalls: 1 }
                }
            );
        }

        res.status(200).json({
            message: "Calls triggered successfully",
            donorsCalled: donors.length,
            donors: donors.map(d => ({  //.map() takes an array and transforms each item into something else, returning a new array
                id: d._id,
                name: d.name,
                phone: d.phone
            }))
        });

    }
    catch (error) {
        // Log the error
        await logAppEvent({
            organizationId: req.user?.organizationId,
            level: "error",
            message: `Error triggering calls: ${error.message}`,
            route: req.originalUrl
        });

        return res.status(500).json({ message: "Internal server error" })
    }
}