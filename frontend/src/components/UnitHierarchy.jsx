import React from 'react';

const UnitHierarchy = ({ unit }) => {
  if (!unit) return <span>N/A</span>;

  // Build hierarchy path
  const getHierarchyPath = (u) => {
    const path = [u.name];
    let current = u.parent;
    while (current) {
      path.unshift(current.name);
      current = current.parent;
    }
    return path;
  };

  const path = getHierarchyPath(unit);

  return (
    <div className="unit-hierarchy">
      <div className="hierarchy-path">
        {path.map((name, index) => (
          <React.Fragment key={index}>
            {index > 0 && <span className="hierarchy-separator">→</span>}
            <span className={`hierarchy-level ${index === path.length - 1 ? 'current' : ''}`}>
              {name}
            </span>
          </React.Fragment>
        ))}
      </div>
    </div>
  );
};

export default UnitHierarchy;
