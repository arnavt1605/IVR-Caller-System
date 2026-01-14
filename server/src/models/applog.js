import mongoose from "mongoose";

const appLogSchema = new mongoose.Schema(
    {
        organizationId: {
            type: mongoose.Schema.Types.ObjectId,
            required: true,
            index: true
        },

        level: {
            type: String,
            enum: ["info", "warn", "error"],
            required: true
        },

        message: {
            type: String,
            required: true
        },

        route: {
            type: String
        }
    },
    { timestamps: true }
);

export default mongoose.model("AppLog", appLogSchema);
