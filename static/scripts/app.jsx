var CivMap = React.createClass({
  render: function() {
    return (
      <div className="civmap">
        {this.props.name}
      </div>
    );
  }
});

ReactDOM.render(
  <CivMap name='Naunet' />,
  document.getElementById('content')
);
