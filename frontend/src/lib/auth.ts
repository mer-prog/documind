import NextAuth from "next-auth";
import Credentials from "next-auth/providers/credentials";
import { SignJWT } from "jose";
import { authConfig } from "./auth.config";

export const { handlers, auth, signIn, signOut } = NextAuth({
  ...authConfig,
  session: { strategy: "jwt" },
  providers: [
    Credentials({
      credentials: {
        email: { label: "Email", type: "email" },
        password: { label: "Password", type: "password" },
      },
      async authorize(credentials) {
        if (!credentials?.email || !credentials?.password) return null;

        try {
          const res = await fetch(
            `${process.env.NEXT_PUBLIC_API_URL}/api/auth/login`,
            {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({
                email: credentials.email,
                password: credentials.password,
              }),
            }
          );

          if (!res.ok) return null;

          const user = await res.json();
          return {
            id: user.id,
            email: user.email,
            name: user.name,
            workspaceId: user.workspace_id,
            role: user.role,
          };
        } catch {
          return null;
        }
      },
    }),
  ],
  callbacks: {
    async jwt({ token, user }) {
      if (user) {
        token.id = user.id as string;
        token.email = user.email as string;
        token.name = user.name as string;
        token.workspaceId = (user as unknown as Record<string, unknown>).workspaceId as string;
        token.role = (user as unknown as Record<string, unknown>).role as string;

        const nextAuthSecret = process.env.NEXTAUTH_SECRET;
        if (!nextAuthSecret) {
          throw new Error("NEXTAUTH_SECRET environment variable is not set");
        }
        const secret = new TextEncoder().encode(nextAuthSecret);
        const accessToken: string = await new SignJWT({
          sub: token.id,
          email: token.email,
          name: token.name,
          workspace_id: token.workspaceId,
        })
          .setProtectedHeader({ alg: "HS256" })
          .setIssuedAt()
          .setExpirationTime("24h")
          .sign(secret);
        token.accessToken = accessToken;
      }
      return token;
    },
    async session({ session, token }) {
      session.user.id = token.id as string;
      session.user.workspaceId = token.workspaceId as string;
      session.user.role = token.role as string;
      session.accessToken = token.accessToken as string;
      return session;
    },
  },
});
