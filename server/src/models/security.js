import mongoose from "mongoose";

const securityLogSchema = new mongoose.Schema(
    {
        organizationId: {
            type: mongoose.Schema.Types.ObjectId,
            required: true,
            index: true
        },

        userId: {
            type: mongoose.Schema.Types.ObjectId,
            required: true
        },

        action: {
            type: String,
            required: true
        },

        ip: String,
        userAgent: String
    },
    { timestamps: true }
);

export default mongoose.model("SecurityLog", securityLogSchema);