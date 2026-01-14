import mongoose from "mongoose";

const callLogSchema = new mongoose.Schema(
    {
        organizationId: {
            type: mongoose.Schema.Types.ObjectId,
            required: true,
            index: true
        },

        donorId: {
            type: mongoose.Schema.Types.ObjectId,
            required: true
        },

        phone: {
            type: String,
            required: true
        },

        callSid: {
            type: String,
            index: true
        },

        status: {
            type: String,
            enum: ["initiated", "answered", "confirmed", "failed"],
            required: true
        },

        duration: Number
    },
    { timestamps: true }
);

callLogSchema.index({ organizationId: 1, createdAt: -1 });
callLogSchema.index({ organizationId: 1, donorId: 1 });

export default mongoose.model("CallLog", callLogSchema);
