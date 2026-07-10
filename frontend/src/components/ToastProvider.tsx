import {
  createContext,
  useContext,
  useState,
} from "react";

type ToastType = "success" | "error";

type Toast = {
  id: number;
  message: string;
  type: ToastType;
};

type ToastContextType = {
  showToast: (message: string, type?: ToastType) => void;
};

const ToastContext = createContext<ToastContextType | null>(null);


export function ToastProvider({
  children,
}: {
  children: ReactNode;
}) {
  const [toasts, setToasts] = useState<Toast[]>([]);


  function showToast(
    message: string,
    type: ToastType = "success"
  ) {
    const id = Date.now();

    setToasts((prev) => [
      ...prev,
      {
        id,
        message,
        type,
      },
    ]);


    setTimeout(() => {
      setToasts((prev) =>
        prev.filter((t) => t.id !== id)
      );
    }, 4000);
  }


  return (
    <ToastContext.Provider value={{ showToast }}>
      {children}


      <div className="toast-container">
        {toasts.map((toast) => (
          <div
            key={toast.id}
            className={`toast ${toast.type}`}
          >
            <span className="toast-message">
              {toast.message}
            </span>

            <button
              className="toast-close"
              onClick={() =>
                setToasts((prev) =>
                  prev.filter((t) => t.id !== toast.id)
                )
              }
            >
              ✕
            </button>

            <div className="toast-progress" />
          </div>
        ))}
      </div>

    </ToastContext.Provider>
  );
}


export function useToast() {
  const context = useContext(ToastContext);

  if (!context) {
    throw new Error(
      "useToast должен использоваться внутри ToastProvider"
    );
  }

  return context;
}