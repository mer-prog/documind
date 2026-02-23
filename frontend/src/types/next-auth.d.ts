import "next-auth";
import "@auth/core/jwt";
import "@auth/core/types";

declare module "next-auth" {
  interface User {
    id: string;
    workspaceId: string;
    role: string;
  }
  interface Session {
    user: User & {
      id: string;
      email: string;
      name: string;
      workspaceId: string;
      role: string;
    };
    accessToken?: string;
  }
}

declare module "next-auth/jwt" {
  interface JWT {
    id: string;
    workspaceId: string;
    role: string;
    accessToken?: string;
  }
}

declare module "@auth/core/jwt" {
  interface JWT {
    id: string;
    workspaceId: string;
    role: string;
    accessToken?: string;
  }
}

declare module "@auth/core/types" {
  interface User {
    id: string;
    workspaceId: string;
    role: string;
  }
  interface Session {
    user: User & {
      id: string;
      email: string;
      name: string;
      workspaceId: string;
      role: string;
    };
    accessToken?: string;
  }
}
