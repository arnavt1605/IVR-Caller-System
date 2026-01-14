import mongoose from "mongoose";

const donorSchema = new mongoose.Schema(
    {
        organizationId: {
            type: mongoose.Schema.Types.ObjectId,
            required: true,
            index: true
        },

        name: {
            type: String,
            required: true
        },

        age: {
            type: Number,
            required: true
        },

        dob: {
            type: Date,
            required: true
        },

        bloodGroup: {
            type: String,
            required: true,
            index: true
        },

        phone: {
            type: String,
            required: true
        },

        location: String,

        lastCalledAt: Date,

        totalCalls: {
            type: Number,
            default: 0
        },

        isActive: {
            type: Boolean,
            default: true
        }
    },
    { timestamps: true }
);

// Unique phone number per organization
donorSchema.index({ organizationId: 1, phone: 1 }, { unique: true });

// Helps donor prioritization
donorSchema.index({ organizationId: 1, bloodGroup: 1, lastCalledAt: 1 });

export default mongoose.model("Donor", donorSchema);
