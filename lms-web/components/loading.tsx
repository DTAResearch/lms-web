export const Loading = () => {
    return (
        <div className="absolute inset-0 bg-white/50 dark:bg-gray-800/50 flex items-center justify-center z-10">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-sky-500 dark:border-sky-400"></div>
        </div>
    )
}