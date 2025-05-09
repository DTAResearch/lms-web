export const Loading = () => {
    return (
        <div className="absolute inset-0 bg-white/50 dark:bg-gray-800/50 flex flex-col items-center justify-center z-10">
            <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-sky-500 dark:border-sky-400"></div>
            <p className="mt-4 pl-2 text-xl text-sky-500 dark:text-sky-400">Đang tải ...</p>
        </div>
    )
}