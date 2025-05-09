"use client"

import {
	Collapsible,
	CollapsibleContent,
	CollapsibleTrigger,
} from "@/components/ui/collapsible"
import {
	DropdownMenu,
	DropdownMenuContent,
	DropdownMenuItem,
	DropdownMenuSeparator,
	DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import {
	SidebarGroup,
	SidebarGroupLabel,
	SidebarMenu,
	SidebarMenuAction,
	SidebarMenuButton,
	SidebarMenuItem,
	SidebarMenuSub,
	SidebarMenuSubButton,
	SidebarMenuSubItem,
	useSidebar,
} from "@/components/ui/sidebar"

import {
	Frame,
	ChevronRight,
	MoreHorizontal,
	ChartNoAxesCombined,
	Bot,
	Users,
	GraduationCap
} from "lucide-react"
import { SiGoogleclassroom } from "react-icons/si";
import Link from "next/link"
import { usePathname } from "next/navigation"
import { cn } from "@/lib/utils"

const projects = [
	{
		name: "Setting",
		url: "#",
		icon: Frame,
	}
]

const navAdmin = [
	{
		title: "Phân tích",
		url: "/admin/analysis",
		icon: ChartNoAxesCombined,
		isActive: false,
		
	},
	{
		title: "Người dùng",
		url: "/admin/users",
		icon: Users,
		// items: [
		// 	{
		// 		title: "Danh sách",
		// 		url: "#",
		// 	},
		// ],
	},
	{
		title: "Trợ lý AI",
		url: "/admin/assistant-ai",
		icon: Bot,
		// items: [
		// 	{
		// 		title: "Danh sách",
		// 		url: "/admin/assistant-ai",
		// 	},
		// ],
	},
	{
		title: "Lớp học",
		url: "/admin/classroom",
		icon: SiGoogleclassroom,
		items: [
			{
				title: "Danh sách",
				url: "/admin/classroom",
			},
		],
	},
	{
		title: "Kiến thức",
		url: "#",
		icon: GraduationCap,
		items: [
			{
				title: "Dash board",
				url: "/admin/dashboard",
			},
		],
	},
]

export function NavAdmin() {
	const { isMobile } = useSidebar()
	const pathname = usePathname()

	return (
		// <SidebarGroup className="group-data-[collapsible=icon]:hidden">
		<SidebarGroup>
			<SidebarGroupLabel>Admin</SidebarGroupLabel>
			<SidebarMenu>
				{navAdmin.map((item) => {
					const isActive = pathname === item.url || pathname?.startsWith(item.url + "/")
					return (
					<Collapsible
						key={item.title}
						asChild
							defaultOpen={item.isActive || isActive}
						className="group/collapsible"
					>
						<SidebarMenuItem>
							<CollapsibleTrigger asChild>
								<Link href={item.url}>
										<SidebarMenuButton 
											tooltip={item.title}
											className={cn(
												"hover:bg-sky-300 hover:text-white dark:hover:bg-sky-700 dark:hover:text-white",
												isActive && "bg-sky-100 text-sky-400 rounded-md hover:bg-sky-300 hover:text-white dark:bg-sky-700 dark:text-sky-300"
											)}
										>
										{item.icon && <item.icon />}
										<p className="w-64 overflow-hidden whitespace-nowrap text-ellipsis">{item.title}</p>
										<ChevronRight className="ml-auto transition-transform duration-200 group-data-[state=open]/collapsible:rotate-90" />
									</SidebarMenuButton>
								</Link>
							</CollapsibleTrigger>
							<CollapsibleContent>
								<SidebarMenuSub>
										{item.items?.map((subItem) => {
											const isSubActive = pathname === subItem.url
											return (
										<SidebarMenuSubItem key={subItem.title}>
													<SidebarMenuSubButton 
														asChild
														className={cn(
															isSubActive && "bg-sidebar-accent text-sidebar-accent-foreground"
														)}
													>
												<a href={subItem.url}>
													<span>{subItem.title}</span>
												</a>
											</SidebarMenuSubButton>
										</SidebarMenuSubItem>
											)
										})}
								</SidebarMenuSub>
							</CollapsibleContent>
						</SidebarMenuItem>
					</Collapsible>
					)
				})}
				<SidebarMenuItem>
					<SidebarMenuButton className="text-sidebar-foreground/70">
						<MoreHorizontal className="text-sidebar-foreground/70" />
						<span>More</span>
					</SidebarMenuButton>
				</SidebarMenuItem>
			</SidebarMenu>
		</SidebarGroup>
	)
}
