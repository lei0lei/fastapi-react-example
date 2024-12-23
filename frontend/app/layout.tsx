"use client"

import { AppSidebar } from "@/components/app-sidebar"
import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbPage,
  BreadcrumbSeparator,
} from "@/components/ui/breadcrumb"
import { Separator } from "@/components/ui/separator"
import {
  SidebarInset,
  SidebarProvider,
  SidebarTrigger,
} from "@/components/ui/sidebar"

import "./styles/global.css"
import { useState } from 'react'
import { useRouter } from "next/navigation"

import DisplayPage from "@/app/display/page"
import AlgorithmsPage from "@/app/algorithms/page"
import FlowsPage from "@/app/flows/page"
import HardwarePage from "@/app/hardware/page"
import PluginsPage from "@/app/plugins/page"
import ProjectPage from "@/app/project/page"
import SettingsPage from "@/app/settings/page"
import ToolsPage from "@/app/tools/page"
import Page from "@/app/page"



export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const [activePage, setActivePage] = useState('Page')
  const router = useRouter()

  const handleNavigate = (page: string, link: string) => {
    setActivePage(page)
    // router.push(link) // 导航到对应的路由
  }

  const renderPageContent = () => {
    switch (activePage) {
      case "Page":
        return <Page />;
      case "Display":
        return <DisplayPage />;
      case "Algorithms":
        return <AlgorithmsPage />;
      case "Flows":
        return <FlowsPage />;
      case "Hardware":
        return <HardwarePage />;
      case "Plugins":
        return <PluginsPage />;
      case "Project":
        return <ProjectPage />;
      case "Settings":
        return <SettingsPage />;
      case "Tools":
        return <ToolsPage />;
      default:
        return <div>Page not found</div>;
    }
  };


  return (
    <html lang="en">
      <body>
        {/* Layout UI */}
        <main>
        <SidebarProvider
          style={
            {
              "--sidebar-width": "300px",
            } as React.CSSProperties
          }
        >
          <AppSidebar onNavigate={handleNavigate} />
          <SidebarInset>
            <header className="sticky top-0 flex shrink-0 items-center gap-2 border-b bg-background p-4">
              <SidebarTrigger className="-ml-1" />
              <Separator orientation="vertical" className="mr-2 h-4" />
              <Breadcrumb>
                <BreadcrumbList>
                  <BreadcrumbItem className="hidden md:block">
                    <BreadcrumbLink href="#">All</BreadcrumbLink>
                  </BreadcrumbItem>
                  <BreadcrumbSeparator className="hidden md:block" />
                  <BreadcrumbItem>
                    <BreadcrumbPage>{activePage}</BreadcrumbPage>
                  </BreadcrumbItem>
                </BreadcrumbList>
              </Breadcrumb>
            </header>
            <div className="flex flex-1 flex-col gap-4 p-4">
              {renderPageContent()}
            </div>
          </SidebarInset>
        </SidebarProvider>
        </main>
      </body>
    </html>
  )
}