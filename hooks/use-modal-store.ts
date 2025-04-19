import { create } from "zustand";

export type ModalType = "createDepartment";

interface ModalStore {
    type: ModalType | null;
    isOpen: boolean;
    isSubmit: boolean;
    data: Record<string, any>;
    onOpen: (type: ModalType, data?: Record<string, any>) => void;
    onClose: () => void;
    onSave: () => void;
}

export const useModal = create<ModalStore>((set) => ({
    type: null,
    data: {},
    isOpen: false,
    isSubmit: false,
    onSave: () => set({ isSubmit: true }),
    onOpen: (type: ModalType, data: Record<string, any> = {}) =>
        set({ type, isOpen: true, data }),
    onClose: () => set({ type: null, isOpen: false, data: {}, isSubmit: false  }),
}));
