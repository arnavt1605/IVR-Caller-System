// Middleware to verify JWT and attach authenticated user to req.user

import jwt from "jsonwebtoken";

export const authMiddleware = (req, res, next) => {
    // Extract the token from the Authorization header
    const authHeader = req.headers.authorization;

    // Verify the token
    if (!authHeader || !authHeader.startsWith("Bearer ")) {
        return res.status(401).json({ message: "Unauthorized" })
    }

    //Split the header into Bearer + <token>
    const token = authHeader.split(" ")[1];

    try {
        const decoded = jwt.verify(token, process.env.JWT_SECRET)

        //Adding a custom user object to the request
        req.user = {
            userId: decoded.userId,
            organizationId: decoded.organizationId,
            role: decoded.role
        };
        next();
    }
    catch (error) {
        return res.status(401).json({ message: "Invalid or expired token" })
    }

}

