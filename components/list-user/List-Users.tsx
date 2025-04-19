'use client';

import React, { useState, useEffect, useCallback } from "react";
import { Search } from "lucide-react";
import { useSession } from "next-auth/react";
import { debounce } from "lodash";
import { API_BASE_URL } from "@/constants/URL";
import { userPerPageOptions } from "@/constants/UserList";
import axiosInstance from "@/lib/Api-Instance";
import { toast } from "sonner";
import Image from "next/image";
import { Input } from "../ui/input";
import {
	Pagination,
	PaginationContent,
	PaginationItem,
	PaginationLink,
	PaginationNext,
	PaginationPrevious,
	PaginationEllipsis
} from "@/components/ui/pagination";
import {
	Select,
	SelectContent,
	SelectGroup,
	SelectItem,
	SelectLabel,
	SelectTrigger,
	SelectValue,
} from "@/components/ui/select"



// Define types
interface User {
	id: string;
	email: string;
	name: string;
	role: string;
	avatar: string;
	created_at: number;
}

interface UserListProps {
	groupId?: string;
	isInGroupView?: boolean;
	isTeacherList?: boolean;
}

const ListUsers: React.FC<UserListProps> = ({
	groupId,
	isInGroupView = false,
	isTeacherList = false
}) => {
	// Auth
	const { data: session, status } = useSession();

	// States
	const [loading, setLoading] = useState(false);
	const [searchQuery, setSearchQuery] = useState("");
	const [searchBy, setSearchBy] = useState("name");
	const [currentPage, setCurrentPage] = useState(1);
	const [usersPerPage, setUsersPerPage] = useState(10);
	const [users, setUsers] = useState<User[]>([]);
	const [totalUsers, setTotalUsers] = useState(0);
	const [isInitialLoad, setIsInitialLoad] = useState(true);

	const roleMap: Record<string, string> = {
		admin: "Admin",
		teacher: "Giáo viên",
		user: "Học sinh"
	};

	// Update user role
	const updateUserRole = async (userId: string, newRole: string) => {
		try {
			setLoading(true);
			const payload = { new_role: newRole.toLowerCase() };

			const response = await axiosInstance.patch(
				`${API_BASE_URL}/users/update-role/${userId}`,
				payload,
				{
					headers: {
						Authorization: `Bearer ${session?.user?.backendToken}`,
						"X-Requested-With": "XMLHttpRequest"
					}
				}
			);

			if (response.status === 200) {
				setUsers(
					users.map((user) =>
						user.id === userId ? { ...user, role: newRole } : user
					)
				);
				// console.log(`Role updated for user ${userId} to ${newRole}`);
				//lấy tên người dùng từ mảng users
				const updatedUser = users.find((user) => user.id === userId);
				if (updatedUser) {
					toast.success(
						// `Cập nhật quyền thành công cho người dùng ${updatedUser.name} thành ${roleMap[newRole]}`
						`Cập nhật quyền thành công cho người dùng ${updatedUser.name}`,

					);
				}

			}
		} catch (error: any) {
			// console.error(
			// 	"Error updating role:",
			// 	error.response?.data?.detail || error.message
			// );
			toast.error(
				`Cập nhật quyền không thành công: ${error.response?.data?.detail || error.message}`,
			);
		} finally {
			setLoading(false);
		}
	};

	// Handle pagination
	const paginate = (pageNumber: number) => setCurrentPage(pageNumber);

	// Fetch users
	const getUsersByPage = async (
		page: number,
		limit: number,
		query: string,
		searchBy: string
	) => {
		let url = "";
		const params = {
			page,
			limit,
			query,
			searchBy,
		};

		if (groupId) {
			url = isTeacherList
				? `${API_BASE_URL}/groups/teachers/${groupId}`
				: `${API_BASE_URL}/groups/members/${groupId}`;
		} else {
			url = `${API_BASE_URL}/users`;
		}

		try {
			setLoading(true);
			const response = await axiosInstance.get(url, {
				params,
				headers: {
					Authorization: `Bearer ${session?.user?.backendToken}`,
					"X-Requested-With": "XMLHttpRequest"
				}
			});

			if (response.status === 200) {
				const usersData = response.data.data.users;
				const total = response.data.data.total;
				setUsers(usersData);
				setTotalUsers(total);
				setCurrentPage(page);
			}
		} catch (error) {
			console.error("Error fetching users:", error);
		} finally {
			setLoading(false);
		}
	};

	// Debounced search
	const debouncedSearch = useCallback(
		debounce((query: string, searchBy: string) => {
			getUsersByPage(1, usersPerPage, query, searchBy);
		}, 500),
		[usersPerPage, groupId, isTeacherList, session]
	);

	// Initial load
	useEffect(() => {
		if (status === "authenticated" && isInitialLoad) {
			getUsersByPage(currentPage, usersPerPage, "", "name")
				.then(() => setIsInitialLoad(false))
				.catch((err) => {
					console.error("Initial load failed:", err);
					setIsInitialLoad(false);
				});
		}
	}, [status, isInitialLoad]);

	// Load on page/size change
	useEffect(() => {
		if (!isInitialLoad && status === "authenticated") {
			getUsersByPage(currentPage, usersPerPage, searchQuery, searchBy);
		}
	}, [currentPage, usersPerPage, status]);

	// Handle search
	useEffect(() => {
		if (!isInitialLoad && status === "authenticated") {
			debouncedSearch(searchQuery, searchBy);
		}
	}, [searchQuery, searchBy, debouncedSearch, status]);

	// Show loading state while authentication is in progress
	if (status === "loading") {
		return <div className="flex justify-center items-center h-64">Loading...</div>;
	}

	// Check if user is authorized
	if (status === "unauthenticated") {
		return <div className="text-red-500">You must be logged in to view this page</div>;
	}

	return (
		<div className="z-0 space-y-4 md:h-[calc(100vh-80px)] h-[calc(100vh-65px)] flex flex-col">
			<div className="relative overflow-x-auto shadow-md sm:rounded-lg flex-1 flex flex-col dark:shadow-gray-700">
				{/* Table header with search and filters */}
				<div className="flex items-center justify-between flex-wrap space-y-4 md:space-y-0 py-4 px-4 bg-white dark:bg-gray-800">
					<div className="flex items-center gap-4">
						<label className="font-medium text-sm dark:text-gray-300">Tìm kiếm theo:</label>
						<label className="flex items-center gap-1 text-sm dark:text-gray-300">
							<input
								type="radio"
								value="name"
								checked={searchBy === "name"}
								onChange={(e) => setSearchBy(e.target.value)}
								className="dark:accent-sky-400"
							/>
							Tên
						</label>
						<label className="flex items-center gap-1 text-sm dark:text-gray-300">
							<input
								type="radio"
								value="email"
								checked={searchBy === "email"}
								onChange={(e) => setSearchBy(e.target.value)}
								className="dark:accent-sky-400"
							/>
							Email
						</label>
					</div>

					<div className="relative w-full md:w-1/5">
						<div className="absolute inset-y-0 start-0 flex items-center ps-3 pointer-events-none">
							<Search className="w-4 h-4 text-gray-500 dark:text-gray-400" />
						</div>
						<Input
							type="text"
							placeholder="Tìm kiếm..."
							value={searchQuery}
							onChange={(e) => setSearchQuery(e.target.value)}
							className="block ps-10 text-sm text-gray-900 dark:text-white border border-gray-300 dark:border-gray-600 rounded-lg md:w-80 w-full bg-gray-50 dark:bg-gray-700 focus:ring-sky-500 focus:border-sky-500 dark:focus:ring-sky-400 dark:focus:border-sky-400"
						/>
					</div>
				</div>

				{/* Loading indicator */}
				{loading && (
					<div className="absolute inset-0 bg-white/50 dark:bg-gray-800/50 flex items-center justify-center z-10">
						<div className="animate-spin rounded-full h-8 w-8 border-b-2 border-sky-500 dark:border-sky-400"></div>
					</div>
				)}

				{/* Table with users */}
				<div className="overflow-y-auto flex-1 dark:bg-gray-800">
					<table className="w-full text-sm text-left text-gray-500 dark:text-gray-400">
						<thead className="text-xs uppercase bg-sky-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 sticky top-0 z-10">
							<tr>
								<th scope="col" className="px-6 py-3 w-[60%]">Người dùng</th>
								{!isInGroupView && <th scope="col" className="px-6 py-3 w-[15%] text-center min-w-[200px]">Loại người dùng</th>}
								<th scope="col" className="px-6 py-3 text-center">Ngày tạo</th>
							</tr>
						</thead>
						<tbody>
							{users.map((user) => (
								<tr key={user.id} className="bg-white border-b hover:bg-gray-50 dark:bg-gray-800 dark:border-gray-700 dark:hover:bg-gray-700">
									<th scope="row" className="flex items-center px-6 py-4 text-gray-900 dark:text-white whitespace-nowrap">
										<Image
											src={user.avatar}
											alt={user.name}
											width={40}
											height={40}
											unoptimized
											className="rounded-full object-cover"
										/>
										<div className="ps-3">
											<div className="text-base font-semibold">{user.name}</div>
											<div className="font-normal text-gray-500 dark:text-gray-400">{user.email}</div>
										</div>
									</th>
									{!isInGroupView && session?.user.role === "admin" && (
										<td className="px-6 py-4 text-center">
											<Select
												value={user.role}
												onValueChange={(value) => updateUserRole(user.id, value)}

											>
												<SelectTrigger className="mx-auto">
													<SelectValue placeholder="Chọn vai trò" />
												</SelectTrigger>
												<SelectContent>
													<SelectGroup>
														<SelectLabel className="text-gray-500 dark:text-gray-400">Loại người dùng</SelectLabel>
														<SelectItem value="admin">Admin</SelectItem>
														<SelectItem value="teacher">Giáo viên</SelectItem>
														<SelectItem value="user">Học sinh</SelectItem>
													</SelectGroup>
												</SelectContent>
											</Select>
										</td>
									)}
									<td className="px-6 py-4 text-center">{user.created_at}</td>
								</tr>
							))}

							{users.length === 0 && !loading && (
								<tr className="bg-white dark:bg-gray-800">
									<td colSpan={isInGroupView ? 4 : 5} className="px-6 py-4 text-center h text-gray-500 dark:text-gray-400">
										{/* <Image
											src="/images/empty.png"
											alt="No data"
											width={100}
											height={100}
											className="mx-auto mb-2"
										/> */}
										<p className="text-md">	Không tìm thấy người dùng nào</p>
									</td>
								</tr>
							)}
						</tbody>
					</table>
				</div>

				{/* Pagination */}
				<div className="border-t border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 px-6 py-4 flex flex-col md:flex-row justify-between items-center gap-4">
					<div className="flex items-center gap-2 text-sm dark:text-gray-300">
						<p className="w-[120px]">Số hàng mỗi trang:</p>
						<Select
							value={usersPerPage.toString()}
							onValueChange={(value) => {
								setCurrentPage(1);
								setUsersPerPage(Number(value));
							}}
						>
							<SelectTrigger className="mx-auto">
								<SelectValue placeholder="10" />
							</SelectTrigger>
							<SelectContent>
								<SelectGroup>
									{userPerPageOptions.map((value) => (
										<SelectItem key={value} value={value.toString()}>
											{value}
										</SelectItem>
									))}
								</SelectGroup>
							</SelectContent>
						</Select>
					</div>

					<Pagination>
						<PaginationContent>
							<PaginationItem>
								<PaginationPrevious
									onClick={() => currentPage > 1 && paginate(currentPage - 1)}
									className={currentPage === 1 ? "pointer-events-none opacity-50" : "cursor-pointer"}
									aria-disabled={currentPage === 1}
								/>
							</PaginationItem>

							{/* First page if not visible */}
							{currentPage > 2 && (
								<PaginationItem>
									<PaginationLink onClick={() => paginate(1)} className="cursor-pointer">
										1
									</PaginationLink>
								</PaginationItem>
							)}

							{/* Ellipsis if needed */}
							{currentPage > 3 && (
								<PaginationItem>
									<PaginationEllipsis />
								</PaginationItem>
							)}

							{/* Previous page if not first */}
							{currentPage > 1 && (
								<PaginationItem>
									<PaginationLink onClick={() => paginate(currentPage - 1)} className="cursor-pointer">
										{currentPage - 1}
									</PaginationLink>
								</PaginationItem>
							)}

							{/* Current page */}
							<PaginationItem>
								<PaginationLink isActive>{currentPage}</PaginationLink>
							</PaginationItem>

							{/* Next page if exists */}
							{currentPage < Math.ceil(totalUsers / usersPerPage) && (
								<PaginationItem>
									<PaginationLink onClick={() => paginate(currentPage + 1)} className="cursor-pointer">
										{currentPage + 1}
									</PaginationLink>
								</PaginationItem>
							)}

							{/* Ellipsis if needed */}
							{currentPage < Math.ceil(totalUsers / usersPerPage) - 2 && (
								<PaginationItem>
									<PaginationEllipsis />
								</PaginationItem>
							)}

							{/* Last page if not visible */}
							{currentPage < Math.ceil(totalUsers / usersPerPage) - 1 && (
								<PaginationItem>
									<PaginationLink
										onClick={() => paginate(Math.ceil(totalUsers / usersPerPage))}
										className="cursor-pointer"
									>
										{Math.ceil(totalUsers / usersPerPage)}
									</PaginationLink>
								</PaginationItem>
							)}

							<PaginationItem>
								<PaginationNext
									onClick={() => currentPage < Math.ceil(totalUsers / usersPerPage) && paginate(currentPage + 1)}
									className={currentPage >= Math.ceil(totalUsers / usersPerPage) || totalUsers === 0 ? "pointer-events-none opacity-50" : "cursor-pointer"}
									aria-disabled={currentPage >= Math.ceil(totalUsers / usersPerPage) || totalUsers === 0}
								/>
							</PaginationItem>
						</PaginationContent>
					</Pagination>
				</div>
			</div>
		</div>
	);
};

export default ListUsers;