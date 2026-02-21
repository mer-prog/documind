import "next-auth";

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
  }
}
