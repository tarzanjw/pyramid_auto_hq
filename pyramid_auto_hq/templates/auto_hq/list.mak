<%inherit file="_layout.mak" />

<%block name="page_title">${view.Object.__name__} list</%block>

<style type="text/css">
.table th {
    font-family: Monaco,Menlo,Consolas,"Courier New",monospace;
    font-size:90%;
}
.col-type-id, .col-type-numeric, .col-type-datetime, .col-type-bool {
    font-family: Monaco,Menlo,Consolas,"Courier New",monospace;
    text-align:right;
    font-size:90%;
}

.col-type-commands a {
    color: inherit;
}
</style>

<%block name="object_list">
<%
    from sqlalchemy import types
    obj = view.Object
    col_types = {}

    for col in obj.__table__.columns:
        attr_name = view.column_to_attribute(col.name)
        if col.name == 'id':
            col_types[attr_name] = 'id'
        elif isinstance(col.type, types.String):
            col_types[attr_name] = 'string'
        elif isinstance(col.type, types.Boolean):
            col_types[attr_name] = 'bool'
        elif isinstance(col.type, types.Integer) or isinstance(col.type, types.Numeric):
            col_types[attr_name] = 'numeric'
        elif isinstance(col.type, types.Date) or isinstance(col.type, types.DateTime):
            col_types[attr_name] = 'datetime'
        else:
            col_types[attr_name] = 'general'
%>
<table class="table table-striped table-bordered table-condensed table-objects">
    <thead>
        <tr>
            <th>Commands</th>
        % for name in view.list_attr_names:
            <th class="col-type-${col_types[name]}">
                ${' '.join([word.capitalize() for word in name.split('_')])}
            </th>
        % endfor
        </tr>
    </thead>
    <tbody>
    % for e in page.items:
        <%
            from pyramid.traversal import ResourceURL
            from pyramid import location
            from pyramid.traversal import resource_path, resource_path_tuple
            r = request.context[e.id]
        %>
        <tr>
            <td class="col-type-commands">
                % if 'detail' in view.actions:
                <a href="${request.resource_url(request.context[e.id])}">
                    <span class="glyphicon glyphicon-eye-open"></span></a>
                % endif
                % if 'update' in view.actions:
                <a href="${request.resource_url(request.context[e.id], 'update')}">
                    <span class="glyphicon glyphicon-edit"></span></a>
                % endif
                % if 'delete' in view.actions:
                <a class="cmd-delete" href="${request.resource_url(request.context[e.id], 'delete')}"
                   data-message="Do you want to delete ${view.Object.__name__} ${e}">
                    <span class="glyphicon glyphicon-remove"></span></a>
                % endif
            </td>
        % for name in view.list_attr_names:
            <td class="col-type-${col_types[name]}">
                ${e.__getattribute__(name)}
            </td>
        % endfor
        </tr>
    % endfor
    </tbody>
</table>
</%block>
<div class="pagination pagination-small pagination-right">
${page.pager(
    format="(Page $page of $page_count) &nbsp;&nbsp; ~3~",
    link_attr={"class":"btn btn-small"},
    dotdot_attr={"class":"btn btn-small disabled"},
    curpage_attr={"class":"btn btn-small disabled"}
)}
</div>
<script type="text/javascript">
jQuery(function($) {
    $('.table-objects .cmd-delete').click(function(e) {
        if (confirm($(this).attr('data-message')))
            return true;
        else {
            e.preventDefault();
            return false;
        }
    })
})
</script>