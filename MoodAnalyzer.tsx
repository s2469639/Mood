import { GoogleGenAI } from "@google/genai";

// AI 초기화
const ai = new GoogleGenAI({ apiKey: process.env.GEMINI_API_KEY });

interface MoodAnalysisResult {
  tempo: "느림" | "보통" | "빠름";
  genre: string;
  moodKeywords: string[];
  recommendedVibe: string;
}
// 
// DFDS
async function analyzeUserMood(userPrompt: string): Promise<MoodAnalysisResult> {
  const systemInstruction = `
    사용자의 입력 문장을 분석하여 음악 추천에 필요한 파라미터를 JSON 형식으로 추출해주세요.
    반드시 아래 JSON 구조로만 응답해주세요.
    {
      "tempo": "느림" | "보통" | "빠름",
      "genre": "추천 장르 (예: 어쿠스틱, 록, 발라드 등)",
      "moodKeywords": ["키워드1", "키워드2"],
      "recommendedVibe": "전체적인 분위기 한 줄 요약"
    }
  `;

  const response = await ai.models.generateContent({
    model: "gemini-2.5-flash",
    contents: userPrompt,
    config: {
      systemInstruction: systemInstruction,
      responseMimeType: "application/json",
    },
  });


  
  try {
    return JSON.parse(response.text.trim()) as MoodAnalysisResult;
  } catch (error) {
    console.error("JSON 파싱 에러:", error);
    throw new Error("무드 분석에 실패했습니다.");
  }
}