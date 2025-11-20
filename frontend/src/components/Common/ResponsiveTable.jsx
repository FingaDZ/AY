import { Table, Card, List, Typography, Space } from 'antd';
import useResponsive from '../../hooks/useResponsive';

const { Text } = Typography;

/**
 * Tableau responsive qui s'adapte automatiquement :
 * - Desktop/Tablette : Table classique
 * - Mobile : Cards/List
 */
const ResponsiveTable = ({ 
  columns, 
  dataSource, 
  loading,
  pagination,
  rowKey = 'id',
  mobileRenderItem,
  onRow,
  ...tableProps 
}) => {
  const { isMobile } = useResponsive();

  // Rendu mobile par défaut si pas de custom render
  const defaultMobileRenderItem = (item) => {
    if (!columns || columns.length === 0) return null;
    
    return (
      <Card 
        size="small" 
        style={{ marginBottom: 12 }}
        hoverable
        onClick={() => onRow && onRow(item)?.onClick && onRow(item).onClick()}
      >
        {columns.map((col) => {
          if (col.hideOnMobile) return null;
          if (col.responsive && !col.responsive.includes('xs')) return null;
          
          const value = col.render 
            ? col.render(item[col.dataIndex], item, 0)
            : item[col.dataIndex];

          if (!value && value !== 0) return null;

          return (
            <div key={col.key || col.dataIndex} style={{ marginBottom: 8 }}>
              <Text strong style={{ fontSize: 12, color: '#666' }}>
                {col.title}:
              </Text>
              <div style={{ marginTop: 4 }}>
                {value}
              </div>
            </div>
          );
        })}
      </Card>
    );
  };

  if (isMobile) {
    return (
      <List
        loading={loading}
        dataSource={dataSource || []}
        pagination={pagination}
        renderItem={mobileRenderItem || defaultMobileRenderItem}
        {...tableProps}
      />
    );
  }

  return (
    <Table
      columns={columns}
      dataSource={dataSource}
      loading={loading}
      pagination={pagination}
      rowKey={rowKey}
      scroll={{ x: 'max-content' }}
      onRow={onRow}
      {...tableProps}
    />
  );
};

export default ResponsiveTable;
