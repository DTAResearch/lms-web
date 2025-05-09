import { create } from "zustand";
import { Models } from "@/components/admin/Assistant-Ai-Page";

export type ModalType = "createAssistant" | "editAssistant" | "deleteAssistant";

interface ModalData {
  groupId?: string;
  modelId?: string;
  title?: string;
  [key: string]: any;
}

interface ModalStore {
  type: ModalType | null;
  data: ModalData;
  isOpen: boolean;
  isSubmit: boolean;
  onOpen: (type: ModalType, data?: any) => void;
  onClose: () => void;
  onSave: () => void;
  cleanupModalEffects: () => void; // Thêm hàm mới để dọn sạch các hiệu ứng modal
}

export const useModal = create<ModalStore>((set) => ({
  type: null,
  data: {},
  isOpen: false,
  isSubmit: false,
  onOpen: (type, data = {}) => {
    // Đảm bảo modal trước đó đã được dọn sạch hoàn toàn
    const cleanup = () => {

      const overlays = document.querySelectorAll('[data-radix-focus-guard]');
      overlays.forEach(el => el.remove());
      

      document.body.removeAttribute('aria-hidden');
      document.documentElement.removeAttribute('data-radix-focus-lock');
      

      document.body.style.pointerEvents = '';
      

      document.body.classList.remove('overflow-hidden');
      
 
      setTimeout(() => {
        set({ 
          isOpen: true, 
          type, 
          data,
          isSubmit: false 
        });
      }, 5); // delay nhỏ để đảm bảo DOM đã được cập nhật
    };
    
    // Nếu đang mở modal khác, đóng nó trước
    set((state) => {
      if (state.isOpen) {
        // Đóng modal hiện tại trước
        setTimeout(cleanup, 100);
        return { isOpen: false };
      } else {
        // Không có modal nào đang mở, có thể mở ngay lập tức
        cleanup();
        return {};
      }
    });
  },
  onClose: () => {
    set({ isOpen: false, type: null });
    
    // Thực hiện dọn dẹp khi đóng modal
    setTimeout(() => {
      const overlays = document.querySelectorAll('[data-radix-focus-guard]');
      overlays.forEach(el => el.remove());
      
      document.body.removeAttribute('aria-hidden');
      document.documentElement.removeAttribute('data-radix-focus-lock');
      document.body.style.pointerEvents = '';
    }, 100);
  },
  onSave: () => {
    set({ isSubmit: true });
  },
  cleanupModalEffects: () => {
    // Dọn dẹp các hiệu ứng modal có thể còn sót lại
    const overlays = document.querySelectorAll('[data-radix-focus-guard]');
    overlays.forEach(el => el.remove());
    
    document.body.removeAttribute('aria-hidden');
    document.documentElement.removeAttribute('data-radix-focus-lock');
    document.body.style.pointerEvents = '';
  }
}));
