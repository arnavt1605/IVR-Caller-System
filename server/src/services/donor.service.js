// Contains business logic for selecting donors for IVR calls

import Donor from "../models/donor.js";

// Select the eligible donors
export const selectDonorForCall = async ({ organizationId, bloodGroup, limit = 10 }) => {
    const donors = await donors.find({ organizationId, bloodGroup, isActive: true }).sort({ lastCalledAt: 1 }).limit(limit);

    return donors;
}

// Order of calling becomes:
// 1. Never-called donors
// 2. Least recently called donors
// 3. Most recently called donors (last)