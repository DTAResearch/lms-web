'use client';

import { useSession } from "next-auth/react";
import { useEffect } from "react";
import Cookies from "js-cookie";

export default function AuthCookieManager() {
  const { data: session } = useSession();
  
  useEffect(() => {
    if (session?.user?.backendToken) {
      // Set the cookie with the backend token (unencoded)
      Cookies.set('access_token', session.user.backendToken, {
        path: '/',
        sameSite: 'lax'
      });
    }
  }, [session]);
  
  return null; // This component doesn't render anything
}