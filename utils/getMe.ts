
import { API_BASE_URL } from '@/constants/URL';
import axiosInstance from '@/lib/Api-Instance';

export const getMe = async () => {
    const res = await axiosInstance.get(`${API_BASE_URL}/users/me`);
    return res.data;
};
