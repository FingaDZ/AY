import { useEffect, useState } from 'react';

/**
 * Hook personnalisé pour gérer le responsive avec matchMedia natif
 * Plus fiable que useBreakpoint sur certains mobiles
 * @returns {Object} Informations sur le breakpoint actuel
 */
export const useResponsive = () => {
  const [windowSize, setWindowSize] = useState({
    width: typeof window !== 'undefined' ? window.innerWidth : 1200,
    height: typeof window !== 'undefined' ? window.innerHeight : 800,
  });

  useEffect(() => {
    console.log('🖥️ Responsive Hook initialized');
    
    const handleResize = () => {
      const width = window.innerWidth;
      const height = window.innerHeight;
      
      setWindowSize({ width, height });
      
      // Log pour debug
      const type = width < 768 ? 'mobile' : width < 992 ? 'tablet' : 'desktop';
      console.log(`🔄 Screen resized: ${width}px - Type: ${type}`);
    };

    // Listener natif pour resize
    window.addEventListener('resize', handleResize);
    
    // Media query listeners pour debug
    const mobileQuery = window.matchMedia('(max-width: 767px)');
    const tabletQuery = window.matchMedia('(min-width: 768px) and (max-width: 991px)');
    
    const handleMobileChange = (e) => {
      if (e.matches) console.log('📱 Mobile mode activated');
    };
    
    const handleTabletChange = (e) => {
      if (e.matches) console.log('📱 Tablet mode activated');
    };
    
    mobileQuery.addEventListener('change', handleMobileChange);
    tabletQuery.addEventListener('change', handleTabletChange);
    
    // Initial call
    handleResize();

    return () => {
      window.removeEventListener('resize', handleResize);
      mobileQuery.removeEventListener('change', handleMobileChange);
      tabletQuery.removeEventListener('change', handleTabletChange);
    };
  }, []);

  const isMobile = windowSize.width < 768;
  const isTablet = windowSize.width >= 768 && windowSize.width < 992;
  const isDesktop = windowSize.width >= 992;
  const isLargeDesktop = windowSize.width >= 1200;

  // Log état actuel
  useEffect(() => {
    const type = isMobile ? 'mobile' : isTablet ? 'tablet' : 'desktop';
    console.log(`📱 Screen type: ${type} (width: ${windowSize.width}px)`);
  }, [isMobile, isTablet, windowSize.width]);

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
