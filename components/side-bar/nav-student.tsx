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
	Bot
} from "lucide-react"
import { SiGoogleclassroom } from "react-icons/si";
import { usePathname } from "next/navigation"
import { cn } from "@/lib/utils"
import Link from "next/link"


const projects = [
	{
		name: "Setting",
		url: "#",
		icon: Frame,
	}
]

const navStudent = [
	{
		title: "Phân tích",
		url: "#",
		icon: ChartNoAxesCombined,
		isActive: false,
		items: [
			{
				title: "Danh sách",
				url: "/admin/account",
			},
		],
	},
	{
		title: "Trợ lý AI",
		url: "#",
		icon: Bot,
		items: [
			{
				title: "Danh sách",
				url: "/admin/department",
			},
			{
				title: "Thêm mới",
				url: "#",
			},
		],
	},
	{
		title: "Lớp học",
		url: "#",
		icon: SiGoogleclassroom,
		items: [
			{
				title: "Lĩnh vực",
				url: "/admin/field",
			},
			{
				title: "Loại văn bản",
				url: "/admin/type",
			},
			{
				title: "Cấp ban hành",
				url: "/admin/release-level",
			},
		],
	},
]

export function NavStudent() {
	const { isMobile } = useSidebar()
	const pathname = usePathname()

	return (
		<SidebarGroup>
			<SidebarGroupLabel>Student</SidebarGroupLabel>
			<SidebarMenu>
				{navStudent.map((item) => {
					const isActive = item.items?.some(subItem => 
						pathname === subItem.url || pathname?.startsWith(subItem.url + "/")
					)
					
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
												"hover:bg-sky-300 hover:text-white",
												isActive && "bg-sky-100 text-sky-400 rounded-md hover:bg-sky-300 hover:text-white"
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
											const isActive = pathname === subItem.url || pathname?.startsWith(subItem.url + "/")
											return (
												<SidebarMenuSubItem key={subItem.title}>
													<SidebarMenuSubButton 
														asChild
														className={cn(
															isActive && "bg-sidebar-accent text-sidebar-accent-foreground"
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
