// Handles IVR call triggering logic for for blood request

import { selectDonorForCall } from "../services/donor.service";
import CallLog from "../models/calllog";
import Donor from "../models/donor";

export const triggerCalls = async (req, res) => {
    try {
        const { bloodGroup, limit } = req.body;
        const organizationId = req.user.organizationId;

        if (!bloodGroup) {
            return res.status(400).json({ message: "Blood group is required" })
        }

        const donors = await selectDonorForCall({ organizationId, bloodGroup, limit });

        if (donors.length === 0) {
            return res.status(404).json({ message: "No donors found", donorsCalled: 0 })
        }

        for (const donor of donors) {
            await CallLog.create({
                organizationId,
                donorId: donor._id,
                phone: donor.phone,
                status: "initiated",
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
        console.log(error);
        return res.status(500).json({ message: "Internal server error" })
    }
}