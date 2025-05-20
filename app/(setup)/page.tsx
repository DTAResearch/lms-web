"use client";

import { useSession } from "next-auth/react";
import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { Role } from "@/constants/Role";
import { Loading } from "@/components/loading";

export default function Dashboard() {
	const { data: session, status } = useSession();
	const router = useRouter();

	useEffect(() => {
		if (session?.user?.backendToken) {
			localStorage.setItem("access_token", session.user.backendToken);
		}
	}, [session]);

	useEffect(() => {
		if (status === "unauthenticated") {
			router.push("/auth/login");
			return;
		}

		if (status === "authenticated" && session?.user) {
			const role = session.user.role;

			// Chuyển hướng dựa trên role
			switch (role) {
				case Role.ADMIN:
					router.push("/admin");
					break;
				case Role.MANAGER:
					router.push("/manager");
					break;
				case Role.DIRECTOR:
					router.push("/director");
				case Role.TEACHER:
					router.push("/teacher");
					break;
				case Role.STUDENT:
					router.push("/student");
					break;
				default:
					// Nếu không có role cụ thể, ở lại dashboard
					break;
			}
		}
	}, [session, status, router]);

	if (status === "loading") {
		return (
			<Loading />
		);
	}

	return (
		<div className="h-screen flex justify-center items-center">
			<p>Chuyển hướng...</p>
		</div>
	);
}