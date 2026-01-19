// Middleware to check user roles


// Higher level middleware 
export const requireRole = (allowedRole = []) => (req, res, next) => {
    const role = req.user?.role;

    if (!role) {
        return res.sendStatus(401); // sends http code + response
    }

    if (!roles.includes(role)) {
        return res.sendStatus(403);
    }

    next();
};
