"use client"

import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "@/components/ui/collapsible"
import {
  SidebarGroup,
  SidebarGroupLabel,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarMenuSub,
  SidebarMenuSubButton,
  SidebarMenuSubItem,
} from "@/components/ui/sidebar"

import {
  ChevronRight,
  MoreHorizontal,
  Users,
  Bot,
  ChartNoAxesCombined,
  GraduationCap
} from "lucide-react"
import { SiGoogleclassroom } from "react-icons/si"
import { usePathname } from "next/navigation"
import { cn } from "@/lib/utils"
import Link from "next/link"
import { Role } from "@/constants/Role"

// Định nghĩa navigation data theo role
const navigationData = {
  admin: {
    label: "Admin",
    items: [
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
      },
      {
        title: "Trợ lý AI",
        url: "/admin/assistant-ai",
        icon: Bot,
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
            title: "Dashboard",
            url: "/admin/dashboard",
          },
        ],
      },
    ]
  },
  teacher: {
    label: "Teacher",
    items: [
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
          {
            title: "Thêm mới",
            url: "/admin/account/create-account",
          },
        ],
      },
      {
        title: "Người dùng",
        url: "#",
        icon: Users,
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
        title: "Trợ lý AI",
        url: "#",
        icon: Bot,
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
      {
        title: "Lớp học",
        url: "#",
        icon: SiGoogleclassroom,
        items: [
          {
            title: "Dashboard",
            url: "/admin/dashboard",
          },
        ],
      },
    ]
  },
  user: {
    label: "Student",
    items: [
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

        ],
      },
    ]
  }
}

interface NavMainProps {
  role: Role;
}

export function NavMain({
  role
}: NavMainProps) {
  const pathname = usePathname()
  // const navData = navigationData[role]
  const navData = navigationData[role as keyof typeof navigationData]

  if (!navData) return null

  return (
    <SidebarGroup>
      <SidebarGroupLabel>{navData.label}</SidebarGroupLabel>
      <SidebarMenu>
        {navData.items.map((item) => {
          const isActive = item.items?.some(subItem =>
            pathname === subItem.url || pathname?.startsWith(subItem.url + "/")
          ) || (pathname === item.url || pathname?.startsWith(item.url + "/"))

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
                      {item.items && <ChevronRight className="ml-auto transition-transform duration-200 group-data-[state=open]/collapsible:rotate-90" />}
                    </SidebarMenuButton>
                  </Link>
                </CollapsibleTrigger>
                {item.items && (
                  <CollapsibleContent>
                    <SidebarMenuSub>
                      {item.items.map((subItem) => {
                        const isSubActive = pathname === subItem.url || pathname?.startsWith(subItem.url + "/")
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
                )}
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
