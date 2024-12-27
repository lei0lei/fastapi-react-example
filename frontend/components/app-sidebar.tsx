"use client"

import * as React from "react"
import { ArchiveX, Command, File, Inbox, Send, Trash2,Tv,FolderKanban,Settings,Blocks,Wrench,Workflow,Cpu,Box  } from "lucide-react"

import { NavUser } from "@/components/nav-user"
import { Label } from "@/components/ui/label"
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupContent,
  SidebarHeader,
  SidebarInput,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  useSidebar,
} from "@/components/ui/sidebar"
import { Switch } from "@/components/ui/switch"
import { useRouter } from 'next/router';
import  { useEffect, useState } from 'react';


import {DisplayPageSidebar} from "@/app/display/page"
import {AlgorithmsPageSidebar} from "@/app/algorithms/page"
import {FlowsPageSidebar} from "@/app/flows/page"
import {HardwarePageSidebar} from "@/app/hardware/page"
import {PluginsPageSidebar} from "@/app/plugins/page"
import {ProjectPageSidebar} from "@/app/project/page"
import {SettingsPageSidebar} from "@/app/settings/page"
import {ToolsPageSidebar} from "@/app/tools/page"

import {History} from "@/app/page"


// This is sample data
const sidebar_items = {
  user: {
    name: "lei0lei",
    email: "lei.lei.fan.meng@gmail.com",
    avatar: "/avatars/shadcn.jpg",
  },
  navMain: [
    {
      title: "Display",
      url: "#",
      icon: Tv,
      isActive: true,
      link: "/display",
    },
    {
      title: "Project",
      url: "#",
      icon: FolderKanban,
      isActive: false,
      link: "/project",
    },
    {
      title: "Settings",
      url: "#",
      icon: Settings,
      isActive: false,
      link: "/settings",
    },
    {
      title: "Plugins",
      url: "#",
      icon: Blocks,
      isActive: false,
      link: "/plugins",
    },
    {
      title: "Tools",
      url: "#",
      icon: Wrench,
      isActive: false,
      link: "/tools",
    },
    {
      title: "Flows",
      url: "#",
      icon: Workflow,
      isActive: false,
      link: "/flows",
    },
    {
      title: "Hardware",
      url: "#",
      icon: Cpu,
      isActive: false,
      link: "/hardware",
    },
    {
      title: "Algorithms",
      url: "#",
      icon: Box,
      isActive: false,
      link: "/algorithms",
    },
  ],
}




interface AppSidebarProps {
  onNavigate: (page: string, link: string) => void
}

export function AppSidebar({ onNavigate, ...props }: AppSidebarProps) {
  // Note: I'm using state to show active item.
  // IRL you should use the url/router.
  const [activeItem, setActiveItem] = React.useState(sidebar_items.navMain[0])
  const { setOpen } = useSidebar()

  const renderPageContent = () => {
    switch (activeItem.title) {
      case "Display":
        return <DisplayPageSidebar />;
      case "Algorithms":
        return <AlgorithmsPageSidebar />;
      case "Flows":
        return <FlowsPageSidebar />;
      case "Hardware":
        return <HardwarePageSidebar />;
      case "Plugins":
        return <PluginsPageSidebar />;
      case "Project":
        return <ProjectPageSidebar />;
      case "Settings":
        return <SettingsPageSidebar />;
      case "Tools":
        return <ToolsPageSidebar />;
      default:
        return <History />;
    }
  };
  
  // const [isClient, setIsClient] = useState(false);  // 用于标记是否在客户端
  // const router = useRouter(); // 获取 Next.js 的路由
  // 在组件加载后，标记客户端渲染完成
  // useEffect(() => {
  //   setIsClient(true);
  // }, []);

  return (
    <Sidebar
      collapsible="icon"
      className="overflow-hidden [&>[data-sidebar=sidebar]]:flex-row"
      {...props}
    >
      {/* This is the first sidebar */}
      {/* We disable collapsible and adjust width to icon. */}
      {/* This will make the sidebar appear as icons. */}
      <Sidebar
        collapsible="none"
        className="!w-[calc(var(--sidebar-width-icon)_+_1px)] border-r"
      >
        <SidebarHeader>
          <SidebarMenu>
            <SidebarMenuItem>
              <SidebarMenuButton size="lg" asChild className="md:h-8 md:p-0">
                <a href="#">
                  <div className="flex aspect-square size-8 items-center justify-center rounded-lg bg-sidebar-primary text-sidebar-primary-foreground">
                    <Command className="size-4" />
                  </div>
                  <div className="grid flex-1 text-left text-sm leading-tight">
                    <span className="truncate font-semibold">Acme Inc</span>
                    <span className="truncate text-xs">Enterprise</span>
                  </div>
                </a>
              </SidebarMenuButton>
            </SidebarMenuItem>
          </SidebarMenu>
        </SidebarHeader>
        <SidebarContent>
          <SidebarGroup>
            <SidebarGroupContent className="px-1.5 md:px-0">
              <SidebarMenu>
                {sidebar_items.navMain.map((item) => (
                  <SidebarMenuItem key={item.title}>
                    <SidebarMenuButton
                      tooltip={{
                        children: item.title,
                        hidden: false,
                      }}
                      onClick={() => {
                        setActiveItem(item)
                        onNavigate(item.title, item.link) // 通知父组件
                        setOpen(true)
                      }}
                      isActive={activeItem.title === item.title}
                      className="px-2.5 md:px-2"
                    >
                      <item.icon />
                      <span>{item.title}</span>
                    </SidebarMenuButton>
                  </SidebarMenuItem>
                ))}
              </SidebarMenu>
            </SidebarGroupContent>
          </SidebarGroup>
        </SidebarContent>
        <SidebarFooter>
          <NavUser user={sidebar_items.user} />
        </SidebarFooter>
      </Sidebar>

      {/* This is the second sidebar */}
      {/* We disable collapsible and let it fill remaining space */}
      {activeItem.title !== "Display" ? (
        <Sidebar collapsible="none" className="hidden flex-1 md:flex">
        <SidebarHeader className="gap-3.5 border-b p-4">
          <div className="flex w-full items-center justify-between">
            <div className="text-base font-medium text-foreground">
              {activeItem.title}
            </div>
          </div>
        </SidebarHeader>



        <SidebarContent>
          <SidebarGroup className="px-0">
            {renderPageContent()}
          </SidebarGroup>
        </SidebarContent>
      </Sidebar>
      ):null}
    </Sidebar>
  )
}
