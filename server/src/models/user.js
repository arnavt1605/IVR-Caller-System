import mongoose from "mongoose";

const userSchema = new mongoose.Schema({
    organizationId: {
        type: mongoose.Schema.Types.ObjectId,
        required: true,
        index: true
    },

    email: {
        type: String,
        required: true,
        index: true
    },

    passwordHash: {
        type: String,
        required: true
    },

    role: {
        type: String,
        enum: ["admin", "staff"],
        default: "staff"
    },

    failedLoginAttempts: {
        type: Number,
        default: 0
    },

    lastLoginAt: Date,
},
    { timestamp: true }
);

userSchema.index(
    { organizationId: 1, email: 1 }, //The index key is the pair (organizationId, email)
    { unique: true } //No two documents can have the same orgid+email pair
)

export default mongoose.model("User", userSchema);