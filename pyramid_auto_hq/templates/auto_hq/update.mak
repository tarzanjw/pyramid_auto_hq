<%inherit file="_layout.mak" />

<%block name="page_title">Update ${view.Object.__name__}#${view.current_object}</%block>

<%block name="form">
<form class="form-horizontal" method="post">
    <fieldset>
        ${form_renderer.smart_render()|n}

        <div class="form-group">
            <div class="col-lg-offset-2 col-lg-10">
                <button type="submit" name="submit" value="update" class="btn btn-primary">Update</button>
            </div>
        </div>
    </fieldset>
</form>
</%block>