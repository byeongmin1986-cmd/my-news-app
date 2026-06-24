import type { Metadata } from "next";
import "./globals.css";
import Navigation from "@/components/Navigation";

export const metadata: Metadata = {
  title: "송파 재건축 갈아타기 분석기",
  description: "인덕원마을삼성 → 송파구 재건축 단지 의사결정 보조 도구",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="ko" className="h-full">
      <body className="min-h-full flex flex-col bg-slate-50">
        <Navigation />
        <main className="flex-1">
          {children}
        </main>
        <footer className="bg-white border-t border-gray-200 py-4 mt-8">
          <div className="max-w-7xl mx-auto px-4 text-center">
            <p className="text-xs text-gray-400">
              ⚠️ 본 앱의 모든 가격·사업 단계 정보는 <strong>모의 데이터</strong>입니다. 실제 투자 결정 전 반드시{" "}
              <strong>국토교통부 실거래가 공개시스템, 서울시 정비사업 정보몽땅, 해당 구청·조합 공식 자료</strong>로 재확인하세요.
              본 앱은 의사결정 보조 도구이며 투자 권유가 아닙니다.
            </p>
          </div>
        </footer>
      </body>
    </html>
  );
}
