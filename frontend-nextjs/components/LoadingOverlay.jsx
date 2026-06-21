export default function LoadingOverlay({ isLoading }) {
  if (!isLoading) return null;
  return (
    <div className="loading-overlay loading-overlay--active">
      <div className="loading-spinner"></div>
      <p className="loading-text">Our AI is analyzing culinary experiences...</p>
    </div>
  );
}
