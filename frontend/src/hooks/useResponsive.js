import { useEffect, useState } from 'react';

/**
 * Hook personnalisé pour gérer le responsive
 * @returns {Object} Informations sur le breakpoint actuel
 */
export const useResponsive = () => {
  const [windowSize, setWindowSize] = useState({
    width: typeof window !== 'undefined' ? window.innerWidth : 1200,
    height: typeof window !== 'undefined' ? window.innerHeight : 800,
  });

  useEffect(() => {
    const handleResize = () => {
      setWindowSize({
        width: window.innerWidth,
        height: window.innerHeight,
      });
    };

    window.addEventListener('resize', handleResize);
    handleResize();

    return () => window.removeEventListener('resize', handleResize);
  }, []);

  const isMobile = windowSize.width < 768;
  const isTablet = windowSize.width >= 768 && windowSize.width < 992;
  const isDesktop = windowSize.width >= 992;
  const isLargeDesktop = windowSize.width >= 1200;

  return {
    isMobile,
    isTablet,
    isDesktop,
    isLargeDesktop,
    width: windowSize.width,
    height: windowSize.height,
  };
};

export default useResponsive;
