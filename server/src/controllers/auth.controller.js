// Handles authentication logic such as user login

import jwt from "jsonwebtokens";
import bcrypt from "bcrypt";
import user from "../models/user.js";

export const login = async (req, res) => {
    const { email, password } = req.body;

    const user = await user.findOne({ email });
    if (!user) {
        return res.status(401).json({ message: "Could not find user" });
    }

    const isMatch = await bcrypt.compare(password, user.passwordHash);
    if (!isMatch) {
        return res.status(401).json({ message: "Invalid credentials" });
    }

    // Generate JWT token by signing the payload with JWT_SECRET
    const token = jwt.sign(
        {
            userId: user._id,
            organizationId: user.organizationId,
            role: user.role
        },
        process.env.JWT_SECRET,
        { expiresIn: "1h" }
    );

    res.json({ token });
}