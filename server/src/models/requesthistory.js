import mongoose from "mongoose";

const requestHistorySchema = new mongoose.Schema(
    {
        organizationId: {
            type: mongoose.Schema.Types.ObjectId,
            required: true,
            index: true
        },

        bloodGroup: {
            type: String,
            required: true
        },

        status: {
            type: String,
            enum: ["IN_PROGRESS", "COMPLETED"],
            default: "IN_PROGRESS"
        },

        totalCalls: Number,
        answeredCalls: Number,
        confirmedCount: Number,

        confirmedDonors: [
            {
                donorId: mongoose.Schema.Types.ObjectId,
                name: String,
                phone: String
            }
        ],

        requestedAt: {
            type: Date,
            default: Date.now
        }
    },
    { timestamps: true }
);

requestHistorySchema.index({ organizationId: 1, requestedAt: -1 });

export default mongoose.model("RequestHistory", requestHistorySchema);
