<%inherit file="../hq/_column2.mak" />
<% from pyramid_auto_hq import model_url %>
<ul>
% for data in models.values():
    <% m = data['model'] %>
    <li><a href="${model_url(m)}">${m.__name__}</a></li>
% endfor
</ul>