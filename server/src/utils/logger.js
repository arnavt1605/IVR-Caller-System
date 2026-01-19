// Helper functions for application and security logging

import AppLog from "../models/applog.js";
import SecurityLog from "../models/securitylog.js";

export const logAppEvent = async ({ organizationId, level, message, route }) => {
    try {
        await AppLog.create({ organizationId, level, message, route });

    }
    catch (error) {
        console.log(error);
    }
}


export const logSecurityEvent = async ({ organizationId, userId, action, ip, userAgent }) => {
    try {
        await SecurityLog.create({ organizationId, userId, action, ip, userAgent });
    }
    catch (error) {
        console.log(error);
    }
}