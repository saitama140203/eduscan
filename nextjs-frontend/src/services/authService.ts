import axios from 'axios';

// URL của API backend, bạn cần thay đổi nếu khác
// TODO: Đưa URL này vào biến môi trường (.env.local)
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

// Định nghĩa kiểu cho response từ API /login
// Dựa trên LoginResponse schema từ backend
export interface LoginApiResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  user_id: number; // Hoặc string, tùy thuộc vào kiểu ID người dùng của bạn
  email: string;
  hoTen: string;
  vaiTro: string;
}

// Định nghĩa kiểu cho request body của API /login (nếu cần tường minh)
// Dựa trên LoginRequest schema từ backend
// export interface LoginPayload {
//   username: string;
//   password: string;
// }

export const loginUser = async (email: string, password: string): Promise<LoginApiResponse> => {
  try {
    const response = await axios.post<LoginApiResponse>(
      `${API_BASE_URL}/auth/login`,
      {
        email, // FastAPI endpoint /login mong đợi { "username": "...", "password": "..." }
        password,
      }
    );
    return response.data;
  } catch (error) {
    // Axios ném lỗi cho các status code ngoài 2xx
    // Bạn có thể xử lý lỗi chi tiết hơn ở đây hoặc để component gọi hàm xử lý
    console.error('API login error:', error);
    throw error; // Ném lại lỗi để component có thể bắt và hiển thị thông báo
  }
};

// Các hàm gọi API khác liên quan đến auth có thể thêm vào đây
// ví dụ: getCurrentUser, logout, requestPasswordReset, confirmPasswordReset 