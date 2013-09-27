<%inherit file="../hq/_column1.mak" />

<%block name="page_header">
<legend>
    <%block name="page_title">There's no title here</%block>
    <small>
      <div class="pull-right">
      % for cmd in view.commands:
        <a href="${cmd['url']}" title="${cmd['label']}"><span class="glyphicon glyphicon-${cmd.get('icon', 'usd')}"></span></a>
      % endfor
      </div>
    </small>
</legend>
</%block>


<%block name="breadcrumbs">
<% entries = view.breadcrumbs %>
% if len(entries):
<ul class="breadcrumb">
% for e in entries:
    % if isinstance(e, basestring):
        <li class="active">${e}</li>
    % else:
    <li><a href=${e['url']}>${e['label']}</a></li>
    % endif
% endfor
</ul>
% endif
</%block>

<%block name="commands">
##    <h4>Commands</h4>
##    <ul class="nav nav-pills nav-stacked">
##    % for label, url in view.commands:
####        <li><a href="${url}">${label}</a></li>
##        <li><a href="${url}" title="${label}"><span class="glyphicon glyphicon-plus"></span></a></li>
##    % endfor
##    </ul>
</%block>
${next.body()}