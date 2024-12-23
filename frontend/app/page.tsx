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


export default function Page() {
  return <div>Welcome to the App</div>;
}

export function History(){
  return <div>init -12-15-2024</div>;

}