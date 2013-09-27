<%inherit file="_layout.mak" />

<%block name="page_title">Create new ${view.Object.__name__}</%block>

<%block name="form">
<form class="form-horizontal" method="post">
    <fieldset>
        ${form_renderer.smart_render()|n}

        <div class="form-group">
            <div class="col-lg-offset-2 col-lg-10">
                <button type="submit" name="submit" value="create" class="btn btn-primary">Create</button>
            </div>
        </div>
    </fieldset>
</form>
</%block>